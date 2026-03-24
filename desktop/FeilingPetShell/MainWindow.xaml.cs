using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;

namespace FeilingPetShell;

public partial class MainWindow : Window
{
    private readonly string _repoRoot;
    private Point _dragStartScreen;
    private Point _dragStartWindow;
    private bool _pointerDown;
    private bool _dragging;

    public MainWindow()
    {
        InitializeComponent();

        _repoRoot = ResolveRepoRoot();
        LoadPetImage();

        Loaded += OnLoaded;
        MouseEnter += (_, _) => AnimatePetScale(1.018, 120);
        MouseLeave += (_, _) =>
        {
            if (!_dragging && !_pointerDown)
            {
                AnimatePetScale(1.0, 140);
            }
        };
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        var workArea = SystemParameters.WorkArea;
        Left = workArea.Right - Width - 24;
        Top = workArea.Bottom - Height - 24;
    }

    private void LoadPetImage()
    {
        var imagePath = Path.Combine(_repoRoot, "assets", "characters", "feiling", "base", "feiling_master_v1.png");
        if (!File.Exists(imagePath))
        {
            throw new FileNotFoundException($"Feiling asset not found: {imagePath}");
        }

        var bitmap = new BitmapImage();
        bitmap.BeginInit();
        bitmap.CacheOption = BitmapCacheOption.OnLoad;
        bitmap.UriSource = new Uri(imagePath, UriKind.Absolute);
        bitmap.EndInit();
        bitmap.Freeze();

        PetImage.Source = bitmap;
    }

    private static string ResolveRepoRoot()
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current is not null)
        {
            if (Directory.Exists(Path.Combine(current.FullName, "assets")) &&
                Directory.Exists(Path.Combine(current.FullName, "scripts")))
            {
                return current.FullName;
            }

            current = current.Parent;
        }

        throw new DirectoryNotFoundException("Could not resolve repository root from WPF output path.");
    }

    private void AnimatePetScale(double scale, int durationMs)
    {
        var easing = new QuadraticEase { EasingMode = EasingMode.EaseOut };
        var animationX = new DoubleAnimation(scale, TimeSpan.FromMilliseconds(durationMs)) { EasingFunction = easing };
        var animationY = new DoubleAnimation(scale, TimeSpan.FromMilliseconds(durationMs)) { EasingFunction = easing };
        PetScaleTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleXProperty, animationX);
        PetScaleTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleYProperty, animationY);
    }

    private void PlayClickFeedback()
    {
        var shrink = new DoubleAnimation(0.985, TimeSpan.FromMilliseconds(70))
        {
            AutoReverse = true,
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
        };

        var rise = new DoubleAnimation(-4, TimeSpan.FromMilliseconds(70))
        {
            AutoReverse = true,
            EasingFunction = new QuadraticEase { EasingMode = EasingMode.EaseOut }
        };

        PetScaleTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleXProperty, shrink);
        PetScaleTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleYProperty, shrink);
        PetTranslateTransform.BeginAnimation(System.Windows.Media.TranslateTransform.YProperty, rise);
    }

    private bool IsMenuSource(object? source)
    {
        if (source is not DependencyObject dependencyObject)
        {
            return false;
        }

        var current = dependencyObject;
        while (current is not null)
        {
            if (current == MenuButton || current == MenuPopup || current == OpenSearchButton)
            {
                return true;
            }

            current = System.Windows.Media.VisualTreeHelper.GetParent(current);
        }

        return false;
    }

    private void OnShellMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        if (IsMenuSource(e.OriginalSource))
        {
            return;
        }

        _pointerDown = true;
        _dragging = false;
        _dragStartScreen = PointToScreen(e.GetPosition(this));
        _dragStartWindow = new Point(Left, Top);
        CaptureMouse();
        AnimatePetScale(0.992, 70);
    }

    private void OnShellMouseMove(object sender, MouseEventArgs e)
    {
        if (!_pointerDown || e.LeftButton != MouseButtonState.Pressed)
        {
            return;
        }

        var screenPoint = PointToScreen(e.GetPosition(this));
        var dx = screenPoint.X - _dragStartScreen.X;
        var dy = screenPoint.Y - _dragStartScreen.Y;

        if (!_dragging && Math.Abs(dx) + Math.Abs(dy) > 4)
        {
            _dragging = true;
        }

        if (!_dragging)
        {
            return;
        }

        Left = _dragStartWindow.X + dx;
        Top = _dragStartWindow.Y + dy;
    }

    private void OnShellMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
    {
        if (!_pointerDown)
        {
            return;
        }

        ReleaseMouseCapture();
        var wasDragging = _dragging;
        _pointerDown = false;
        _dragging = false;

        if (wasDragging)
        {
            AnimatePetScale(1.0, 100);
            return;
        }

        PlayClickFeedback();
        AnimatePetScale(1.0, 140);
    }

    private void MenuButton_OnClick(object sender, RoutedEventArgs e)
    {
        MenuPopup.IsOpen = !MenuPopup.IsOpen;
    }

    private async void OpenSearchButton_OnClick(object sender, RoutedEventArgs e)
    {
        MenuPopup.IsOpen = false;

        var scriptPath = Path.Combine(_repoRoot, "scripts", "start_search_window.ps1");
        var psi = new ProcessStartInfo
        {
            FileName = "powershell",
            Arguments = $"-ExecutionPolicy Bypass -File \"{scriptPath}\"",
            WorkingDirectory = _repoRoot,
            UseShellExecute = false,
            CreateNoWindow = true,
            WindowStyle = ProcessWindowStyle.Hidden
        };

        Process.Start(psi);
        await Task.CompletedTask;
    }

    private void MenuPopup_OnClosed(object? sender, EventArgs e)
    {
        if (!_pointerDown)
        {
            AnimatePetScale(1.0, 120);
        }
    }
}
